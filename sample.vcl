# Use 4.0 format
vcl 4.0;

# Default upstream
backend default {
    .host = "127.0.0.1";
    .port = "8080";
}

# Access control
acl purge {
    "localhost";
    "127.0.0.1";
}

# vcl_recv adapted from the Varnish default
sub vcl_recv {
    if (req.method == "PURGE") {
        if (!client.ip ~ purge) {
            return(synth(405, "Not allowed."));
        }
        return(purge);
    }

    if (req.method == "PRI") {
        # We do not support SPDY or HTTP/2.0
        return(synth(405));
    }

    if (req.method != "GET" &&
      req.method != "HEAD" &&
      req.method != "PUT" &&
      req.method != "POST" &&
      req.method != "TRACE" &&
      req.method != "OPTIONS" &&
      req.method != "DELETE") {
        # Non-RFC2616 or CONNECT which is weird
        return(pipe);
    }

    if (req.method != "GET" && req.method != "HEAD") {
        # We only deal with GET and HEAD by default
        return(pass);
    }
    if (req.http.Authorization) {
        # Not cacheable by default
        return(pass);
    }
    return(hash);
}

sub vcl_backend_response {
    # Make no assumptions about the state of vary before hand. All that is
    # needed, is to temporarily replace Cookie in the Vary header while it
    # gets passed through the rest of the Varnish functions.
    set beresp.http.Original-Vary = beresp.http.Vary;
    set beresp.http.Vary = regsub(beresp.http.Vary, "Cookie", "Substitute");
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
        # Django cache headers may not set the cookie directly because that
        # leads to a Set-Cookie header. Varnish interprets the presence of that
        # header as a "do not cache" instruction, which would defeat the entire
        # purpose of what we are doing.
        if (resp.http.X-Hash-Cookies) {
            set resp.http.Set-Cookie = "hashcookies=" + resp.http.X-Hash-Cookies;
        }
    }

    # Replace the original Vary header on the response
    set resp.http.Vary = resp.http.Original-Vary;

    # Unset the backup just in case
    unset resp.http.Original-Vary;
}

sub vcl_hash {
    # Cache even with cookies present. Note we don't delete the cookies. Also,
    # we only consider cookies listed in the cookie named hashcookies as part
    # of the hash. This list is determined by the relevant Django Cache Headers
    # policy.
    set req.http.Hash-Cookies = regsub(req.http.Cookie, ".*hashcookies=([^;]+).*", "\1");
    set req.http.Hash-Value = "x";
    if (req.http.Hash-Cookies) {
        # todo: softcode these checks
        if (req.http.Hash-Cookies ~ "messages") {
            if (req.http.Cookie ~ "messages=") {
                set req.http.Hash-Value = req.http.Hash-Value + regsub(req.http.Cookie, ".*messages=([^;]+).*", "\1");
            }
        }
        if (req.http.Hash-Cookies == "messages|isauthenticated") {
            if (req.http.Cookie ~ "isauthenticated=") {
                set req.http.Hash-Value = req.http.Hash-Value + regsub(req.http.Cookie, ".*isauthenticated=([^;]+).*", "\1");
            }
        }
        else if (req.http.Hash-Cookies == "messages|sessionid") {
            if (req.http.Cookie ~ "sessionid=") {
                set req.http.Hash-Value = req.http.Hash-Value + regsub(req.http.Cookie, ".*sessionid=([^;]+).*", "\1");
            }
        }
    }
    hash_data(req.http.Hash-Value);
    unset req.http.Hash-Cookies;
    unset req.http.Hash-Value;
}

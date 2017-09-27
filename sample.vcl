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
    # Make no assumptions about the state of Vary before hand. All that is
    # needed is to temporarily remove Cookie from the Vary header while it
    # gets passed through the rest of the varnish functions.
    set beresp.http.Original-Vary = beresp.http.Vary;
    set beresp.http.Vary = regsub(beresp.http.Vary, "Cookie", "Substitute");
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    # Replace the original Vary header on the response
    set resp.http.Vary = resp.http.Original-Vary;

    # Unset the backup just in case
    unset resp.http.Original-Vary;
}

include "/path/to/generated.vcl";

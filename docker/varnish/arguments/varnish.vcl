vcl 4.0;

import directors;
import std;

{% macro setup_backends_and_director(director_name, director_type, backends) -%}

sub vcl_init {
    new {{ director_name }}_director = directors.{{ director_type }}();
}
{% for backend in backends %}
backend {{ backend|backend_name(director_name) }} {
    .host = "{{ backend.hostname }}";
    .port = "{{ backend.port }}";
}

sub vcl_init {
    {{ director_name }}_director.add_backend({{ backend|backend_name(director_name)}});
}
{% endfor %}

{%- endmacro %}

{{ setup_backends_and_director("django", "round_robin", DJANGO_HOSTS) }}

sub export_log_variables {
    std.log("client_ip:" + client.ip);
    std.log("reason:" + resp.reason);
}

sub vcl_hit {
    set req.http.x-cache-handling = "hit";
}

sub vcl_miss {
    set req.http.x-cache-handling = "miss";
}

sub vcl_pass {
    set req.http.x-cache-handling = "pass";
}

sub vcl_pipe {
    set req.http.x-cache-handling = "pipe:uncacheable";
}

sub vcl_recv {
    unset req.http.x-cache-handling;
    set req.backend_hint = django_director.backend();

    {% if VARNISH_IS_FIRST_HTTP_SERVER %}
    if (std.port(server.ip) == 443) {
        set req.http.X-Forwarded-Proto = "https";
    } else {
        set req.http.X-Forwarded-Proto = "http";
    }
    {% endif %}

    if (req.url ~ "^/_health/") {
        {% if HEALTH_ENABLED %}
            if (client.ip !~ health_acl) {
                return(synth(403, "Access denied."));
            }
            else {
                if (req.url ~ "^/_health/cache") {
                    return(synth(700));
                }
            }
        {% else %}
            return(synth(403, "Access denied."));
        {% endif %}
    }
}

sub vcl_backend_response {
    # this is temporary, since we have no caching scheme currently
    set beresp.ttl = 0s;
}

{% if HEALTH_ENABLED %}
acl health_acl {
    {% for acl in HEALTH_ACLS %}
        {{ acl }};
    {% endfor %}
}
{% endif %}


sub vcl_synth {
    set req.http.x-cache-handling = "synth:synth";
    if (resp.status == 700) {
        set resp.status = 200;
        set resp.reason = "OK";
        set resp.http.Content-Type = "text/plain;";
        call export_log_variables;

        synthetic( {"HTTP 200. Varnish is up!"} );
        return (deliver);
    }
}


sub vcl_deliver {
    set resp.http.X-Request-ID = req.http.X-Request-ID;

    if (obj.uncacheable) {
        set req.http.x-cache-handling = req.http.x-cache-handling + ":uncacheable" ;
    } else {
        set req.http.x-cache-handling = req.http.x-cache-handling + ":cached" ;
    }
    call export_log_variables;
}

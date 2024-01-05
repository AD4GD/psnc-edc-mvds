# ConfigMaps and Secrets

Each Deployment (and Stateful) pulls environment from the it's dedicated ConfigMap and Secret. In Ansible implementation and in following documentation ConfigMaps and Secrets are often treated in a unified way under ``parameters`` name.

ConfigMap and Secret are named using following pattern application-deployment, thus
configmap and secret used by deployment ``django`` of application ``edc-connector`` are named edc-connector-django.

Each Deployment and Stateful set mounts all entries from their respective ConfigMap and Secret using envFrom K8S wording.
Some containers may use parameters from other Deployment or StatefulSet.

In general existance of both ConfigMaps and Secrets is optional. However, some specific entries are obligatory (like DATABASE_USER used in pgbouncer container inside django pod).

Ansible deployment reads definitions of parameters found in inventory files, and constructs definitions of entries. If there are no entries found for a given ConfigMap or Secret, it will not be created.
If the user defines manually some entries, they will be overwritten or may be left untouched (if inventory definition uses ``when_missing`` wording - more on this below).

After each ConfigMap and Secret update, a digest of their current value is obtained and passed as a parameters_digest label into the POD definition, causing Deployment or StatefulSet to start rolling update. Manual change of entry done by user using K8S interfaces will not schedule such behaviour, but any new POD create will see new entries values. Operator may manually delete some POD and just wait a moment for K8S to schedule new POD with new settings. Once such manual changes are considered final, they should be defined back in to the repository (in case of ConfigMaps).

Explicitly defining Secret entries values in inventory files discourached. Secret entries should generated using random lookups or be placed directly into the Secret by operator, either manually or using other script.

## Defining ConfigMaps and Secrets entries

Entries of ConfigMaps and Secrets are defined in the inventory files using following wording:

```
django_configmap__10_more_settings:
  ENTRY_NAME: fixed-entry-value

  # value of OTHER_ENTRY inside application-django-configmap will be set using given value
  # only when it is not yet defined in application-django-configmap
  OTHER_ENTRY:
    when_missing: fixed-entry-value-set-only-when-missing-in-the-configmap

  DATABASE_HOST: "{{ application }}-postgres"

django_configmap__20_even_mores_settings:
  # when the value RANDOM_ENTRY is missing in the configmap,
  # it will be filled by value randomly generated using following lookup
  RANDOM_ENTRY:
    when_missing: "{{ lookup('password', '/dev/null length=12 chars=ascii_letters,digits')}}"

django_secret__10_some_keypair:
  SOME_PRIVATE_KEY_BASE64:
    when_missing:
      generator: "keypair"
      arguments:
        public_key_parameter_name: SOME_PUBLIC_KEY

```

For each component (like django, varnish, postgres) and each parameter kind (secret and configmap) inventory is searched for dictionaries named like ``component_kind__two_digit_number_comment``, then variables are pulled from those dictionaries. Entries from dictionaries with higher priority number override those with the lower priority number. The default priority number of entries defined in application ``group_vars`` should always be 10.


## Implementation

All pods are labeled in a following idiom:
```
  metadata:
    labels:
      parameters_digest: "{{ (django_configmap_digest + django_secret_digest)|hash('sha1') }}"
```

parameters_digest comprises of concatenation of digests of all configmaps and secrets meaningful to the deployment. Concatenation is hashed to overcome limitation o K8S labels size of 63 characters.

## Following configuration

Labels parameters_digest should be removed from logging to decrease overall logging size.

## Caveats

# Readiness and liveness probes

[https://blog.colinbreck.com/kubernetes-liveness-and-readiness-probes-how-to-avoid-shooting-yourself-in-the-foot/]
[https://lorinhochstein.wordpress.com/2017/06/24/a-conjecture-on-why-reliable-systems-fail/]


rootProject.name = "edc-connector"

pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
        mavenLocal()
    }
}

include("launchers:dcp")
include("extensions:did-example-resolver")

include("extensions:policy-engine")
include("extensions:data-plane-oauth2-access-token")
include("extensions:catalog-proxy")
include("extensions:did-example-resolver")
include("extensions:superuser-seed")
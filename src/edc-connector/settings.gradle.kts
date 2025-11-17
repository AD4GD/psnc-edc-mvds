
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
include("extensions:dcp-impl")

include("extensions:policy-engine")
include("extensions:data-plane-oauth2-access-token")

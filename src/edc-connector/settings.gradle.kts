
rootProject.name = "AD4GD-Demo"

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

include("core:base")
include("launchers:daps")
include("launchers:no-daps")
include("launchers:dcp")
include("launchers:identity-hub")
include("extensions:connector-persistence")
include("extensions:policy-engine")
include("extensions:data-plane-oauth2-access-token")
include("extensions:catalog-proxy")
include("extensions:did-example-resolver")

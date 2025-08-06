rootProject.name = "federated-catalog"

include(":core:base")
include(":launchers:daps")
include(":launchers:dcp")
include(":launchers:no-daps")
include(":extensions:target-node-directory-sql")
include(":extensions:catalog-node-static-resolver")
include(":extensions:catalog-node-resolver")
include(":extensions:did-example-resolver")
include(":extensions:dcp-impl")

// this is needed to have access to snapshot builds of plugins
pluginManagement {
    repositories {
        mavenLocal()
        maven {
            url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenLocal()
        maven {
            url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
        }
        mavenCentral()
    }
}

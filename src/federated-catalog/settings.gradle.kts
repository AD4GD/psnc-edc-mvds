rootProject.name = "federated-catalog"

include(":core:base")
include(":launchers:catalog-iam-daps")
include(":launchers:catalog-iam-mocked")
include(":extensions:catalog-node-resolver")
include(":extensions:seed-in-memory-vault")
include(":extensions:target-node-directory-sql")

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

plugins {
    java
    `java-library`
}

val annotationProcessorVersion: String by project
val metaModelVersion: String by project

// these values are required for the project POM (for publishing)
val edcScmConnection: String by project
val edcScmUrl: String by project

buildscript {
    dependencies {
        classpath(libs.edc.build.plugin)
    }
}

val edcVersion = libs.versions.edc

allprojects {

    apply(plugin = "${group}.edc-build")

    // configure which version of the annotation processor to use. defaults to the same version as the plugin
    configure<org.eclipse.edc.plugins.autodoc.AutodocExtension> {
        processorVersion.set(edcVersion)
        outputDirectory.set(project.buildDir)
    }

    configure<org.eclipse.edc.plugins.edcbuild.extensions.BuildExtension> {
        swagger {
            title.set("Registration Service REST API")
            description = "Registration Service REST APIs - merged by OpenApiMerger"
            outputFilename.set(project.name)
            outputDirectory.set(file("${rootProject.projectDir.path}/resources/openapi/yaml"))
        }
    }

    configure<CheckstyleExtension> {
        configFile = rootProject.file("resources/checkstyle-config.xml")
        configDirectory.set(rootProject.file("resources"))
    }

    tasks.test {
        testLogging {
            showStandardStreams = true
        }
    }
}

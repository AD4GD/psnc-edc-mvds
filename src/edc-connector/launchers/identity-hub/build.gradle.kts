
plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {    
    runtimeOnly(libs.bundles.identityhub)
    runtimeOnly(libs.edc.api.observability)
    runtimeOnly(libs.edc.vault.hashicorp)
    runtimeOnly(project(":extensions:superuser-seed"))

    runtimeOnly(libs.bundles.identity.api)

    implementation(libs.bundles.did)
    implementation(project(":extensions:did-example-resolver"))
    implementation(libs.bundles.connector)
    implementation(libs.edc.ih.spi.store)
    implementation(libs.edc.identity.vc.ldp)
    implementation(libs.edc.ih.lib.credentialquery)
    implementation(libs.edc.configuration.filesystem)

    // STS embedded
    runtimeOnly(libs.bundles.sts)
    runtimeOnly(libs.edc.sts.api.accounts)
    runtimeOnly(libs.edc.api.core)
    runtimeOnly(libs.edc.api.version)
}

application {
    mainClass.set("$group.boot.system.runtime.BaseRuntime")
}

var distTar = tasks.getByName("distTar")
var distZip = tasks.getByName("distZip")

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    mergeServiceFiles {
        include("META-INF/services/*")
        include("META-INF/edc/*")
    }
    archiveFileName.set("connector.jar")
    dependsOn(distTar, distZip)
}

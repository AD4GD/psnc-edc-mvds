
plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    runtimeOnly(libs.bundles.identityhub)
    runtimeOnly(libs.edc.api.observability)

    runtimeOnly(libs.bundles.identity.api)

    implementation(libs.edc.configuration.filesystem)
    implementation(libs.bundles.did)
    implementation(project(":extensions:did-example-resolver"))
    implementation(libs.bundles.connector)
    implementation(libs.edc.ih.spi.store)
    implementation(libs.edc.identity.vc.ldp)
    implementation(libs.edc.ih.lib.credentialquery)
}

application {
    mainClass.set("$group.boot.system.runtime.BaseRuntime")
}

var distTar = tasks.getByName("distTar")
var distZip = tasks.getByName("distZip")

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    mergeServiceFiles()
    archiveFileName.set("connector.jar")
    dependsOn(distTar, distZip)
}

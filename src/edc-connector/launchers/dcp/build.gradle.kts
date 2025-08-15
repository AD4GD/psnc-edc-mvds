
plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    implementation(project(":core:base"))
    implementation(project(":extensions:connector-persistence"))
    implementation(project(":extensions:did-example-resolver"))
    
    // used for protected assets dataplane token
    implementation(libs.edc.oauth2.client)

    // DCP
    implementation(libs.edc.dcp.core)
    implementation(libs.edc.spi.identity.trust)
    implementation(libs.edc.spi.transform)
    implementation(libs.edc.spi.catalog)
    implementation(libs.edc.spi.identity.did)
    implementation(libs.edc.lib.jws2020)
    implementation(libs.edc.lib.transform)
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

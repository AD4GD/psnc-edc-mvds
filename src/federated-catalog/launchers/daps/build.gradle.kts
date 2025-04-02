plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    implementation(project(":core:base"))
    // implementation(libs.psnc.vault.keys.seeder)
    
    // OAuth2 DAPS
    implementation(libs.edc.oauth2.core)
    implementation(libs.edc.oauth2.daps)
}

application {
    mainClass.set("$group.boot.system.runtime.BaseRuntime")
}

var distTar = tasks.getByName("distTar")
var distZip = tasks.getByName("distZip")

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    mergeServiceFiles()
    archiveFileName.set("fc.jar")
    dependsOn(distTar, distZip)
}
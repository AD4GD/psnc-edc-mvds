plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    //implementation(libs.psnc.vault.keys.seeder)

    // Federated catalog
    implementation(project(":extensions:catalog-node-resolver"))
    implementation(project(":extensions:did-example-resolver"))

    // some patches/impls for DCP
    implementation(project(":extensions:dcp-impl"))

    implementation(libs.edc.spi.core) // we need some constants

    implementation(libs.bundles.controlplane)
    implementation(libs.bundles.dcp)
    implementation(libs.edc.core.connector)
    implementation(libs.edc.core.token)

    /*
    if (project.properties.getOrDefault("persistence", "false") == "true") {
        runtimeOnly(libs.edc.vault.hashicorp)
        runtimeOnly(libs.bundles.sql.edc)
        runtimeOnly(libs.bundles.sql.fc)
        runtimeOnly(libs.edc.sts.remote.client)
        println("This runtime compiles with a remote STS client, Hashicorp Vault and PostgreSQL. You will need properly configured Postgres and HCV instances.")
    }
    */
    runtimeOnly(libs.bundles.dpf)
    runtimeOnly(libs.edc.api.version)

    //
    implementation(libs.edc.config.filesystem)

    runtimeOnly(libs.edc.vault.hashicorp)
    runtimeOnly(libs.edc.dcp.sts.client)
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

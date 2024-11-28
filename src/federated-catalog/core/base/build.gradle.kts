plugins {
    `java-library`
}

dependencies {
    runtimeOnly(libs.edc.federated.catalog.core)
    runtimeOnly(libs.edc.federated.catalog.spi)
    runtimeOnly(libs.edc.federated.catalog.api)

    runtimeOnly(libs.edc.lib.util)
    runtimeOnly(libs.edc.spi.jsonld)
    runtimeOnly(libs.bundles.edc.connector)
    runtimeOnly(libs.edc.core.controlplane)
    runtimeOnly(libs.edc.core.jetty)
    runtimeOnly(libs.edc.core.token)
    runtimeOnly(libs.edc.lib.providers.jersey)
    runtimeOnly(libs.edc.lib.boot)
    implementation(libs.edc.config.filesystem)

    implementation(project(":extensions:catalog-node-resolver"))
}

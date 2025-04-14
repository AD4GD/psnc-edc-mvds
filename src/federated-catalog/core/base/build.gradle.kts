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

    implementation(project(":extensions:target-node-directory-sql"))
    implementation(libs.edc.fc.catalog.cache.sql)
    implementation(libs.edc.dsp.catalog.http.dispatcher)
    implementation(libs.edc.sql.transaction.local)
    implementation(libs.postgresql)
    implementation(libs.flyway.core)
    implementation(libs.edc.sql.pool)

    implementation(libs.psnc.auth.composite)
    implementation(libs.psnc.vault.keys.seeder)
}

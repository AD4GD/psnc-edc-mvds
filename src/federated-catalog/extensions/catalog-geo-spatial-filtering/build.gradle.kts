plugins {
    `java-library`
}

dependencies {
    implementation("org.eclipse.edc:runtime-metamodel:0.14.0")
    implementation("org.eclipse.edc:core-spi:0.14.0")
    implementation("org.eclipse.edc:sql-lib:0.14.0")
    implementation("com.fasterxml.jackson.core:jackson-databind")

    implementation(libs.bundles.edc.sql.federatedcatalog)

    implementation("org.eclipse.edc:federated-catalog-cache-sql:0.14.0")
}
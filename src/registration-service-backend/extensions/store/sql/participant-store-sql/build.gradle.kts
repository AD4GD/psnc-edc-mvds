plugins {
    `java-library`
}

dependencies {
    implementation(project(":spi:registration-service-store-spi"))
    implementation(libs.edc.spi.transaction)
    implementation(libs.edc.spi.transaction.datasource)
    implementation(libs.edc.core.sql)

    implementation(libs.edc.sql.bootstrapper)

    testImplementation(libs.edc.core.junit)
    testImplementation(testFixtures(libs.edc.core.sql))
    testImplementation(testFixtures(project(":spi:registration-service-store-spi")))
    testImplementation(testFixtures(project(":spi:registration-service-spi")))
}

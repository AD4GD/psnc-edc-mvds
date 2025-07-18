plugins {
    `java-library`
}

dependencies {
    api(project(":spi:registration-service-store-spi"))
    api(libs.edc.spi.transaction)

    implementation(project(":core:identity-provider-client"))
    implementation(project(":core:federated-catalog-client"))

    implementation(libs.edc.core.stateMachine)
    implementation(libs.edc.ext.http)
    //implementation(libs.edc.ext.identity.did.crypto)
    //implementation(libs.ih.ext.verifier.jwt)
    //implementation(libs.ih.ext.credentials.jwt)
    implementation(libs.edc.jwt.verifiable.credentials)

    implementation(libs.opentelemetry.instrumentation.annotations)

    testImplementation(testFixtures(project(":spi:registration-service-spi")))
    testImplementation(testFixtures(project(":spi:registration-service-store-spi")))
    testImplementation(testFixtures(project(":core:registration-service-client")))
}

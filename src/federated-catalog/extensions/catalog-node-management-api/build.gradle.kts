plugins {
    `java-library`
}

dependencies {
    implementation("org.eclipse.edc:crawler-spi:0.14.0")
    implementation("org.eclipse.edc:web-spi:0.14.0")

    // If your module doesn't already get JAX-RS from the runtime:
    implementation("jakarta.ws.rs:jakarta.ws.rs-api:3.1.0")
}
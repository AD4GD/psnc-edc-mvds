plugins {
    `java-library`
}

dependencies {
    api(libs.edc.spi.transaction)
    api(libs.edc.spi.transaction.datasource)
    api(libs.edc.core.sql)
}


plugins {
    `java-library`
}

dependencies {
    // register SQL
    implementation(libs.edc.core.spi)
    implementation(libs.edc.sql.core)

    // Adds Database-Related EDC-Extensions (EDC-SQL-Stores, JDBC-Driver, Pool and Transactions)
    implementation(libs.edc.control.plane.sql)
    implementation(libs.edc.transaction.local)
    implementation(libs.postgresql)
    implementation(libs.flyway.core)

    implementation(libs.edc.sql.pool.apache.commons)

    // apply migrations from tractusX
    implementation(libs.tractus.postgresql.data.plane.migration)
    implementation(libs.tractus.postgresql.control.plane.migration)
}

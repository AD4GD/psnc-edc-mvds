
package org.psnc.mvd.fc.store.statements;

import static java.lang.String.format;

public class DatasetCatalogSqlStatements {

    public String getTargetNodeTable() {
        return "edc_federated_catalog";
    }

    public String getIdColumn() {
        return "id";
    }

    public String getCatalogColumn() {
        return "catalog";
    }

    public String getMarkedColumn() {
        return "marked";
    }

    public String getDeleteDatasetCatalogCacheTemplate() {
        return format("DELETE FROM %s WHERE %s=?",
                    getTargetNodeTable(),
                    getIdColumn());
    }
}

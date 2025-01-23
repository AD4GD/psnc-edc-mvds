
package org.psnc.mvd.fc.store.statements;

import static java.lang.String.format;

public class TargetNodeDirectorySqlStatements {

    public String getTargetNodeTable() {
        return "edc_target_node_directory";
    }

    public String getIdColumn() {
        return "id";
    }

    public String getNameColumn() {
        return "name";
    }

    // connector's protocol url
    public String getTargetUrlColumn() {
        return "target_url";
    }

    public String getSupportedProtocolsColumn() {
        return "supported_protocols";
    }

    public String getInsertTargetNodeTemplate() {
        return format("INSERT INTO %s (%s, %s, %s, %s) VALUES (?,?,?,?::json)",
                    getTargetNodeTable(),
                    getIdColumn(), getNameColumn(), getTargetUrlColumn(), getSupportedProtocolsColumn());
    }

    public String getDeleteTargetNodeTemplate() {
        return format("DELETE FROM %s WHERE %s=?",
                    getTargetNodeTable(),
                    getIdColumn());
    }

    public String getSelectTargetNodeProtocolUrl() {
        return format("SELECT %s FROM %s WHERE %s=?",
                    getTargetUrlColumn(),
                    getTargetNodeTable(),
                    getIdColumn()
        );
    }
}

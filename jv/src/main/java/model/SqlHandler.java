package model;

import lombok.Data;
import org.apache.commons.beanutils.BeanUtils;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Data
public class SqlHandler {
    private String url;
    private String username;
    private String password;
    private final String driverName = "com.mysql.cj.jdbc.Driver";

    private Connection conn;

    public void initConn() throws ClassNotFoundException, SQLException {
        Class.forName(driverName);
        this.conn = DriverManager.getConnection(url, username, password);
    }

    public List<Map<String, Object>> execute(String sql) throws SQLException {
        List<Map<String, Object>> res = new ArrayList<>();
        Statement st = conn.createStatement();
        ResultSet rs = st.executeQuery(sql);
        ResultSetMetaData md = rs.getMetaData();
        int columnCount = md.getColumnCount();

        while (rs.next()) {
            Map<String, Object> ansMap = new HashMap<>();
            for (int i = 1; i <= columnCount; i++) {
                String columnName = md.getColumnName(i);
                Object columnValue = rs.getObject(i);
                ansMap.put(columnName, columnValue);
            }
            res.add(ansMap);
        }
        return res;
    }

    public void close() throws SQLException {
        try {
            conn.close();
        }catch (Exception ignored){}
    }


}

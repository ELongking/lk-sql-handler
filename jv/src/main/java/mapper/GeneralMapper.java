package mapper;

import model.SqlHandler;

import java.sql.Array;
import java.sql.SQLException;
import java.util.*;

public class GeneralMapper {

    public static List<String> getAllDbs(SqlHandler sqlHandler) throws SQLException {
        List<Map<String, Object>> res = sqlHandler.execute("SHOW DATABASES");
        List<String> dbs = new ArrayList<>();
        String[] excludeDbs = {"sys", "information_schema", "mysql", "performance_schema"};
        for (Map<String, Object> item : res) {
            for (Object val : item.values()) {
                if (!Arrays.asList(excludeDbs).contains((String) val)) {
                    dbs.add((String) val);
                }
            }
        }
        return dbs;
    }

    public static List<String> getAllTbs(SqlHandler sqlHandler, String db) throws SQLException {
        List<Map<String, Object>> res = sqlHandler.execute("SHOW TABLES FROM " + db);
        List<String> dbs = new ArrayList<>();
        for (Map<String, Object> item: res){
            for (Object val : item.values()){
                dbs.add((String) val);
            }
        }
        return dbs;

    }
}

package mapper;

import model.SqlHandler;

import java.util.List;
import java.util.Map;

public class InfoMapper {
    public static List<Map<String, Object>> getAllInfo(SqlHandler sqlHandler, String db ,String tb) throws Exception {
        return sqlHandler.execute("SHOW COLUMNS FROM " + db + "." + tb);
    }
}

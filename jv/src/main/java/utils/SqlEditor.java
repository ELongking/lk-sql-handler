package utils;

import model.CommonResult;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

public class SqlEditor {
    public static String urlEditor(String url, String port) {
        return "jdbc:mysql://" + url + ":" + port;
    }

    public static CommonResult<List<Map<String, Object>>> rawResultEnhance(List<Map<String, Object>> oriRes){
        CommonResult<List<Map<String, Object>>> res = new CommonResult<>();
        res.setData(oriRes);
        res.setCode(0);
        res.setMsg("OK");
        return res;
    }

    public static CommonResult<List<Map<String, Object>>> rawResultEnhance(SQLException e){
        CommonResult<List<Map<String, Object>>> res = new CommonResult<>();
        res.setData(null);
        res.setCode(e.getErrorCode());
        res.setMsg(e.getMessage());
        return res;
    }
}

package utils;

import java.lang.reflect.Field;
import java.util.Map;
import java.util.Set;

public class MapToEntity {

    public static <T> T process(Map<String, Object> map, Class<T> c) throws Exception {
        T t = c.newInstance();
        Set<Map.Entry<String, Object>> entries = map.entrySet();
        for (Map.Entry<String, Object> entry : entries) {
            Field f = c.getDeclaredField(entry.getKey());
            f.setAccessible(true);
            f.set(t, entry.getValue());
        }
        return t;
    }
}

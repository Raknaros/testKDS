-- Funciones para la inserción de datos para el sistema de pedidos

-- 1. Función para insertar un pedido principal y devolver su ID
CREATE OR REPLACE FUNCTION insert_pedido(
    v_cliente_test TEXT,
    v_hora_entrega TEXT,
    v_destino TEXT,
    v_importe_total NUMERIC,
    v_observaciones TEXT
) RETURNS INTEGER AS $$
DECLARE
    new_pedido_id INTEGER;
BEGIN
    INSERT INTO orders (cliente_test, hora_entrega, destino, importe_total, observaciones, status, created_at)
    VALUES (v_cliente_test, v_hora_entrega, v_destino, v_importe_total, v_observaciones, 'pending', NOW())
    RETURNING id INTO new_pedido_id;
    RETURN new_pedido_id;
END;
$$ LANGUAGE plpgsql;

-- 2. Función para insertar los detalles (items) de un pedido
CREATE OR REPLACE FUNCTION insert_detalle_pedido(
    v_pedido_id INTEGER,
    v_producto_test TEXT,
    v_cantidad INTEGER,
    v_precio NUMERIC,
    v_notas TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO order_items (v_pedido_id, v_producto_test, v_cantidad, v_precio, v_notas)
    VALUES (v_pedido_id, v_producto_test, v_cantidad, v_precio, v_notas);
END;
$$ LANGUAGE plpgsql;

-- 3. Función para insertar la información del pago
CREATE OR REPLACE FUNCTION insert_pago(
    v_pedido_id INTEGER,
    v_metodo TEXT,
    v_importe NUMERIC,
    v_estado TEXT,
    v_fecha_hora TIMESTAMP
) RETURNS VOID AS $$
BEGIN
    INSERT INTO payments (v_pedido_id, v_metodo, v_importe, v_estado, v_fecha_hora)
    VALUES (v_pedido_id, v_metodo, v_importe, v_estado, v_fecha_hora);
END;
$$ LANGUAGE plpgsql;

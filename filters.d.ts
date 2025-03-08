type ProductFilters = {
  //order?: "asc" | "desc"; // Ordenar por precio o nombre
  //client?: string; // Filtro por cliente
  //store?: string; // Filtro por tienda
  //category?: string; // Filtro por categoría
  //priceRange?: { min?: number; max?: number }; // Rango de precios
  dateRange?: { start?: string; end?: string }; // Rango de fechas
  //state?: string; // Filtro por estado del producto
  //search?: string; // Búsqueda por nombre o descripción
};

type OrderFilters = {
  //id?: string; // Filtro por ID de la orden
  //clientId?: string; // Filtro por ID del cliente
  //managerId?: string; // Filtro por ID del gerente
  //state?: string; // Filtro por estado de la orden
  //dateRange?: { start?: string; end?: string }; // Rango de fechas de entrega
  //totalCostRange?: { min?: number; max?: number }; // Rango de costos totales
};

type PackageFilters = {
  //id?: string; // Filtro por ID del paquete
  //agentId?: number; // Filtro por ID de la agencia
  //rasterId?: string; // Filtro por ID del raster
  //state?: string; // Filtro por estado del paquete
  //productIds?: string[]; // Filtro por IDs de productos (si se desea filtrar por productos específicos)
};

type DeliveryFilters = {
  //id?: number; // Filtro por ID de la entrega
  //clientId?: string; // Filtro por ID del cliente
  //deliveryState?: string; // Filtro por estado de la entrega (por ejemplo, "en camino", "entregado", etc.)
  //payState?: string; // Filtro por estado de pago (por ejemplo, "pagado", "pendiente", etc.)
  costRange?: { min?: number; max?: number }; // Rango de costos de entrega
  //dateRange?: { start?: string; end?: string }; // Rango de fechas de entrega
  //weightRange?: { min?: number; max?: number }; // Rango de peso de los productos
};

type ShopFilters = {
  //id?: string; // Filtro por ID de la compra
  //idStoreOrder?: string; // Filtro por ID de la orden de la tienda
  //state?: string; // Filtro por estado de la compra (por ejemplo, "completada", "pendiente", etc.)
  //totalCostRange?: { min?: number; max?: number }; // Rango de costos totales
  //storeId?: string; // Filtro por ID de la tienda
  //accountId?: string; // Filtro por ID de la cuenta
  //productId?: number | string; // para obtener la compra en la que este un producto en especifico
};

def get_product_commission(product):

        # Product level commission
        if (
            product.commission_type is not None
            and product.commission_value is not None
        ):
            return {
                "type": product.commission_type,
                "value": product.commission_value
            }

        # Category level commission
        if product.category:
            return {
                "type": product.category.commission_type,
                "value": product.category.commission_value
            }

        # Default
        return {
            "type": None,
            "value": 0
        }
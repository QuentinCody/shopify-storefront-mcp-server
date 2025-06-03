# Shopify Storefront MCP Server

This server provides access to the Shopify Storefront API via MCP, allowing AI assistants to query and interact with your Shopify store data.

## Features

- Access to product, collection, and inventory data
- Cart creation and management
- Support for GraphQL queries and mutations
- Automatic token handling and validation
- Easy integration with MCP-compatible AI assistants
- Enhanced token discovery with optional headless browsing

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. (Optional) Install browsers for Playwright: `playwright install`
4. Copy `.env.example` to `.env` and configure your environment variables
5. Generate a Storefront API token via Shopify Admin (see below)
6. Run the server: `python -m shopify_storefront_mcp_server`

## Environment Variables

Create a `.env` file using the provided `.env.example` as a template:

```
# Required
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your_storefront_token
SHOPIFY_STORE_NAME=your-store-name

# Optional
SHOPIFY_API_VERSION=2025-04
SHOPIFY_BUYER_IP=127.0.0.1
```

## Generating a Storefront API Token

1. Log in to your Shopify admin
2. Go to **Apps and sales channels** > **Develop apps** > **Create an app**
3. Name your app (e.g., "MCP Storefront")
4. Go to **API credentials** > **Configure Storefront API scopes**
5. Select necessary scopes:
   - `unauthenticated_read_product_listings`
   - `unauthenticated_read_product_inventory`
   - `unauthenticated_read_product_pricing`
   - `unauthenticated_write_checkouts`
   - `unauthenticated_read_content`
6. Save and copy the generated Storefront API access token
7. Add the token to your `.env` file as `SHOPIFY_STOREFRONT_ACCESS_TOKEN`

## Usage Examples

Running with the MCP server:

```
python -m shopify_storefront_mcp_server
```


The server exposes the following MCP tools:

- `shopify_discover`: Detect if a URL belongs to a Shopify storefront and discover authentication tokens. Pass `use_browser=True` for JS-heavy sites.
- `shopify_storefront_graphql`: Execute GraphQL queries against the Storefront API
- `customer_data`: Unified tool for all customer data operations (Create, Read, Update, Delete)

### Customer Resources

This server also provides MCP resources for customer information:

- `customer://name`: Customer's full name
- `customer://email`: Customer's email address
- `customer://phone`: Customer's phone number
- `customer://shipping_address`: Customer's shipping address (including address1, address2, city, state, postal_code, country)
- `customer://billing_address`: Customer's billing address (including address1, address2, city, state, postal_code, country)
- `customer://profile`: Complete customer profile

Customer data is stored in `user_data/customer.json` and should be managed using the `customer_data` tool.

### Managing Customer Data

The server provides a unified `customer_data` tool for managing all customer information. This tool consolidates create, read, update, and delete operations into a single interface.

Examples:

```
# Get all customer data
customer_data(operation="get")

# Get a specific field
customer_data(operation="get", field="name")
customer_data(operation="get", field="shipping_address")

# Update a specific field
customer_data(operation="update", field="name", value="Jane Doe")
customer_data(
    operation="update",
    shipping_address={
        "address1": "123 Main St",
        "address2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "US"
    }
)

# Add custom fields
customer_data(
    operation="update",
    custom_fields={
        "preferences": {
            "theme": "dark",
            "notifications": "email",
            "language": "en-US"
        },
        "loyalty_tier": "gold",
        "last_purchase_date": "2023-06-15"
    }
)

# Get a custom field
customer_data(operation="get", field="preferences")
customer_data(operation="get", field="loyalty_tier")

# Update single custom field
customer_data(operation="update", field="loyalty_tier", value="platinum")

# Delete a specific field
customer_data(operation="delete", field="phone")
customer_data(operation="delete", field="preferences")

# Delete all customer data
customer_data(operation="delete")
```

This consolidated tool simplifies integration with AI assistants by providing a consistent interface for all customer data operations, including both standard customer information and any custom fields that may be useful for personalization.

### Data Privacy & Storage

Customer data is stored in `user_data/customer.json`. This file contains personal information and should not be committed to version control. The repository includes:

- `user_data/customer.json.example`: A template file showing the expected structure with dummy data
- Entries in `.gitignore` to prevent accidental commits of actual customer data

When deploying this server, the `user_data/customer.json` file will be created automatically when the `customer_data` tool is first used. You can also copy and rename the example file to get started:

```bash
cp user_data/customer.json.example user_data/customer.json
```

All data stored in the customer file persists between server restarts. The file supports both standard customer fields (name, email, addresses) and arbitrary custom fields for AI personalization.

### Creating Checkouts with Customer Data

The server makes it easy to create Shopify checkouts that include customer information by combining the `customer_data` and `shopify_storefront_graphql` tools.

Example workflow:

```
# Step 1: Get customer data
customer_profile = customer_data(operation="get")

# Step 2: Create a cart with GraphQL
cart_mutation = """
mutation createCart($lines: [CartLineInput!]!) {
  cartCreate(input: {lines: $lines}) {
    cart {
      id
      checkoutUrl
    }
    userErrors {
      field
      message
    }
  }
}
"""

cart_variables = {
  "lines": [
    {
      "merchandiseId": "gid://shopify/ProductVariant/12345678901234",
      "quantity": 1
    }
  ]
}

cart_result = shopify_storefront_graphql(
  mode="execute",
  host="your-store.myshopify.com",
  token="your_storefront_token",
  query=cart_mutation,
  variables=cart_variables
)

# Step 3: Apply customer attributes to the cart
cart_id = # extract from cart_result
customer_info = json.loads(customer_profile)

attributes_mutation = """
mutation updateCartAttributes($cartId: ID!, $attributes: [AttributeInput!]!) {
  cartAttributesUpdate(cartId: $cartId, attributes: $attributes) {
    cart {
      id
      checkoutUrl
    }
    userErrors {
      field
      message
    }
  }
}
"""

attributes_variables = {
  "cartId": cart_id,
  "attributes": [
    {
      "key": "email",
      "value": customer_info["email"]
    },
    {
      "key": "deliveryAddress",
      "value": json.dumps(customer_info["shipping_address"])
    }
  ]
}

shopify_storefront_graphql(
  mode="execute",
  host="your-store.myshopify.com",
  token="your_storefront_token",
  query=attributes_mutation,
  variables=attributes_variables
)
```

This approach gives you complete control over the checkout process while leveraging the stored customer information.

## Troubleshooting

If you encounter authentication errors:

1. Verify token format: Storefront API tokens should start with `shpsa_` (newer) or `shpat_` (older)
2. Check store name: Ensure SHOPIFY_STORE_NAME is correct (without .myshopify.com)
3. Check API version: Make sure the API version is supported
4. Test token: Use cURL to test your token directly:
   ```
   curl -X POST \
     https://your-store.myshopify.com/api/2025-04/graphql.json \
     -H "Content-Type: application/json" \
     -H "X-Shopify-Storefront-Access-Token: your_token" \
     -d '{"query": "query { shop { name } }"}'
   ```
5. Regenerate token: If issues persist, create a new token with proper scopes

## Security Considerations

- Never commit your `.env` file or any files containing API tokens
- Use environment variables for all sensitive information
- Consider setting up IP restrictions in your Shopify Admin
- Review the permissions granted to your Storefront API token


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("shopify_storefront", version="0.4.0")

# Import submodules so that tools/resources are registered when package is loaded
from . import customer  # noqa: F401
from . import discovery  # noqa: F401

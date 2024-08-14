"""
Run the app
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app.base:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        ws="websockets",
        log_config="./log_conf.yaml",
    )

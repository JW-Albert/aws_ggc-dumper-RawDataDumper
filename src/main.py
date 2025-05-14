import argparse
import logging
import sys
import traceback
import time

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2

from dumper import Dumper

logger = logging.getLogger(__name__)

def configure_logging(log_level: str):
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=level)
    logger.setLevel(level)

def main():
    parser = argparse.ArgumentParser(description="DIOMap Greengrass component")

    parser.add_argument("--thing-name",
                        type=str,
                        required=True,
                        help="Greengrass Thing name")

    parser.add_argument("--shadow-name",
                        type=str,
                        required=True,
                        help="Greengrass shadow name")

    parser.add_argument("--log-level",
                        type=str,
                        default="INFO",
                        help="Log level (default: INFO)")

    parser.add_argument("--rawdata-topic",
                        type=str,
                        required=True,
                        help="Topic to read raw data")

    parser.add_argument("--write-rule",
                        type=str,
                        required=True,
                        help="Rule to write data")
    
    parser.add_argument("--save-directory",
                        type=str,
                        default="/mnt/rawdata",
                        help="Directory to save CSV files (default: /mnt/rawdata)")

    args = parser.parse_args()

    configure_logging(args.log_level)

    try:
        # 設定與初始化
        ipc_client = GreengrassCoreIPCClientV2()
        dio_map = Dumper(ipc_client, args.thing_name , args.shadow_name, args.rawdata_topic, args.write_rule, args.save_directory)

        # 初始化 GPIO 狀態
        dio_map.init_shadow_state()
        logger.info(f"Initial GPIO state: {dio_map.current_gpio_state}")

        # 訂閱 shadow 變更
        dio_map.subscribe_shadow_topic()
        logger.info(f"Subscribed to shadow topic: {args.shadow_name}")

        # 訂閱 rawdata
        dio_map.subscribe_rawdata_topic()
        logger.info(f"Subscribed to feature topic: {args.rawdata_topic}")

        # Prevent exit to keep subscription alive
        while True:
            time.sleep(10) # 一定要加，不然 CPU 會爆掉

    except Exception as e:
        logger.error("Fatal error: %s", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
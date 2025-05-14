import json
import csv
import logging
import traceback
import time
import math
from pathlib import Path

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import SubscriptionResponseMessage
from awsiot.greengrasscoreipc.model import JsonMessage ,PublishMessage

logger = logging.getLogger(__name__)

class Dumper:
    def __init__ ( self ,ipc_client: GreengrassCoreIPCClientV2 ,thing_name: str ,shadow_name: str ,rawdata_topic: str ,write_rule: str ,save_directory: str ) -> None:
        self.ipc_client = ipc_client
        self.thing_name = thing_name
        self.shadow_name = shadow_name
        self.rawdata_topic = rawdata_topic
        self.write_rule = write_rule
        self.rules = {
            self.write_rule : 1
        }
        self.current_gpio_state = None
        self.save_directory = save_directory
        self.timestamp = int( time.time() * 1000 )

        self.tag_tmp = 0


    def init_shadow_state ( self ) -> None :
        try:
            response = self.ipc_client.get_thing_shadow (
                thing_name = self.thing_name,
                shadow_name = self.shadow_name
            )
            
            shadow_json = json.loads ( response.payload.decode ( "utf-8" ) )
            self.current_gpio_state = shadow_json.get("state" ,{}).get("reported" ,{}).get("gpio_state" ,[])
            logger.info ( f"[Init] Got initial gpio_state from shadow: {self.current_gpio_state}" )
        except Exception as e:
            logger.error ( "Failed to get initial shadow state: %s" ,e )
            traceback.print_exc ()


    def _on_rawdata_stream_event ( self ,event: SubscriptionResponseMessage ) -> None :
        try:
            msg = event.json_message.message # {"timestamp":1.7459860725371535E9,"feature_interval":1.0,"n_extracted_sps":12845.0,"n_feature":1.0,"n_channel":3.0,"data":{"rms":{"X":8.899282026856554E-4,"Y":3.0311158468426244E-4,"Z":4.081027119857277E-4}}}

            gpio_state_str = ''.join(str(i) for i in self.current_gpio_state) if isinstance(self.current_gpio_state ,list) else str(self.current_gpio_state)
            tag = self.rules.get ( f"GPIOState-{gpio_state_str}" ,0 )

            logger.debug ( f"[RawDataReader] Using gpio_state: {gpio_state_str} ,Tag: {tag}" )

            if (tag == 1 and self.tag_tmp == 0) :
                self.timestamp = int( time.time() * 1000 )
                self.save_to_csv( msg )
                self.tag_tmp = 1
                logger.info( f"[RawDataReader] Tag changed to 1 ,saving data to CSV: {self.timestamp}" )
            
            elif (tag == 1 and self.tag_tmp == 1) :
                self.save_to_csv(msg)
                logger.info( f"[RawDataReader] Tag is still 1 ,saving data to CSV: {self.timestamp}" )

            elif ( self.tag_tmp == 1 and tag == 0 ) :
                self.tag_tmp = 0
                self.now_time = int( time.time() * 1000 )
                logger.info( f"[RawDataReader] Tag changed to 0 ,resetting timestamp: {self.now_time}" )

        except Exception as e:
            logger.error( "Error in RawData_Topic message: %s" ,e )
            traceback.print_exc ()

    def _on_shadow_stream_event ( self ,event: SubscriptionResponseMessage ) -> None :
        try:
            msg_str = event.binary_message.message.decode ( "utf-8" )
            msg = json.loads(msg_str)
            logger.info( f"[ShadowTopic] Received shadow update: {msg}" )
            self.current_gpio_state = msg.get( "state" ,{} ).get( "reported" ,{} ).get( "gpio_state" ,[] )
            logger.info( f"[ShadowTopic] Updated gpio_state: {self.current_gpio_state}" )
        except Exception as e:
            logger.error( "Error in shadow_topic message: %s" ,e )
            traceback.print_exc()

    def subscribe_shadow_topic ( self ) -> None :
        self.ipc_client.subscribe_to_topic (
            topic = f"$aws/things/{self.thing_name}/shadow/name/imPHMGPIOState/update/accepted" ,
            on_stream_event = self._on_shadow_stream_event ,
            on_stream_error = self._on_stream_error ,
            on_stream_closed = self._on_stream_closed
        )

    def subscribe_rawdata_topic ( self ) -> None :
        self.ipc_client.subscribe_to_topic (
            topic = self.rawdata_topic ,
            on_stream_event = self._on_rawdata_stream_event ,
            on_stream_error = self._on_stream_error ,
            on_stream_closed = self._on_stream_closed
        )

    def save_to_csv (self ,data: dict) -> None :
        try :
            if ( self.tag_tmp == 0 ) :
                ts = data.get ( "timestamp")
                self.timestamp = math.floor(ts)
                logger.debug ( f"[CSVRiter] Timestamp: {ts} Type: {type(ts)}" )
                sr = data.get ( "sample_rate" )
                dl = data.get ( "data_len" )
                dh = data.get ( "data_header" )        # e.g. "X,Y,Z"
            
            body = data.get ( "data" ,[] )

            target_dir = Path ( self.save_directory )
            target_dir.mkdir( parents = True ,exist_ok = True )
            file_path = target_dir / f"{self.timestamp}.csv"

            with open ( file_path ,mode="a" ,newline="" ,encoding="utf-8" ) as f :
                writer = csv.writer ( f )

                # 1) metadata header + metadata row
                if ( self.tag_tmp == 0 ) :
                    writer.writerow ( ["timestamp" ,"sample_rate" ,"data_len" ,"data_header"] )
                    writer.writerow ( [ts ,sr ,dl ,dh] )
                    writer.writerow ( [] )
                    headers = dh.split ( "," )
                    writer.writerow ( headers )
                    logger.info ( "[CSVRiter] Writing metadata header and row" )

                # 2) 每筆 X,Y,Z 寫成一行
                for row in body:
                    writer.writerow ( row )

            logger.info ( f"Data saved to CSV: {file_path}" )
        except Exception as e :
            logger.error ( "Error saving data to CSV: %s" ,e )
            traceback.print_exc ()

    def _on_stream_error ( self ,error: Exception ) -> bool :
        logger.error( "Stream error: %s" ,error )
        traceback.print_exc ()
        return False

    def _on_stream_closed ( self ) -> None :
        logger.info ( "Subscription stream closed." )
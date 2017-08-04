import java.util.Properties;
import java.util.Arrays;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.ConsumerRecord;

public class ConsumerHardCoded 
{
	 public static void main(String[] args) throws Exception 
	 {
	
		  Properties props = new Properties();
	     
	      props.put("bootstrap.servers", "localhost:9092");
	      props.put("group.id", "test");
	      props.put("enable.auto.commit", "true");
	      props.put("auto.commit.interval.ms", "1000");
	      props.put("session.timeout.ms", "30000");
	      props.put("key.deserializer", "org.apache.kafka.common.serializa-tion.StringDeserializer");
	      props.put("value.deserializer", "org.apache.kafka.common.serializa-tion.StringDeserializer");
	     
	
		 KafkaConsumer<String,String> consumer=null;
		 
		 consumer = new KafkaConsumer<String,String>(props);
		 consumer.subscribe(Arrays.asList("test-topic"));
	     int i = 0;
	     
	     while (true) 
	     {
	         ConsumerRecords<String, String> records = consumer.poll(100);
	         for (ConsumerRecord<String, String> record : records)
	         
	          //print the offset,key and value for the consumer records.
	        	 AfterConsumer.main(record.key());
	         //System.out.printf("offset = %d, key = %s, value = %s\n", record.offset(), record.key(), record.value());
	      }
	}
}
import java.util.Properties;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
public class SimpleProducer 
{
   public static void main(String[] args) throws Exception
   {
	   setProperty();
	   sendMessage();
   }
   
   void setProperty()
   {
	   Properties props = new Properties();
	      props.put("bootstrap.servers", "localhost:9092");
	      props.put("acks", "all");
	      props.put("retries", 0);
	      props.put("batch.size", 16384);
	      props.put("linger.ms", 1);
	      props.put("buffer.memory", 33554432);
	      props.put("key.serializer", "org.apache.kafka.common.serializa-tion.StringSerializer");
	      props.put("value.serializer", "org.apache.kafka.common.serializa-tion.StringSerializer");
   }
   
   void sendMessage()
   {
	   String b="test-topic";
	  String topicName=b,c="1";
	  
	  Producer<String,String> producer,producer1 ;
	  
      producer = new Producer<String, String>(props);
    
      for(int i = 0; i < 10; i++)
      {
    	  ProducerRecord<String,String> rec=new ProducerRecord<String,String>(topicName,Integer.toString(i),Integer.toString(i));
    	  producer.send(rec);
      }
       producer1 = new Producer<String, String>(props);
      
      for(int i = 0; i < 10; i++)
      {
    	  ProducerRecord<String,String> rec1=new ProducerRecord<String,String>("test",Integer.toString(i),Integer.toString(i));
    	  producer1.send(rec1);
    	  
    	  producer.send(rec1);
    	  
      }
      System.out.println("Message sent successfully");
      producer.close();
   }
}
package test.kafka;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import kafka.producer.ProducerConfig;

import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;


public class KafkaProducer {
    Producer<Integer, String> producer;
    private final Properties properties = new Properties();

    public KafkaProducer() {
        properties.put("metadata.broker.list", "localhost:9092");
        properties.put("serializer.class", "kafka.serializer.StringEncoder");
        properties.put("request.required.acks", "1");
        producer = new Producer<Integer,String>(new ProducerConfig(properties));
    }

    public static void main(String[] args) {
        new SimpleProducer();
        String topic = "topic";
        String msg = args[1];
        KeyedMessage<Integer, String> data = new KeyedMessage<Integer,String>(topic, msg);
        producer.send(data);
        producer.close();
    }
}
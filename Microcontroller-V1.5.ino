#include "WiFi.h";
#include <driver/i2s.h>

uint8_t id[6];
const char* ssid = "----";
const char* password =  "----";
const uint16_t port = 8000;
const char * host = "192.168.0.112";


i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 44100,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0};


static const i2s_pin_config_t i2s_mic_pins = {
    .bck_io_num = 26,
    .ws_io_num = 22,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = 21
};


void setup()
{
  esp_efuse_read_mac(id);
 
  
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &i2s_mic_pins);
  
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
}





int findLength(int32_t num)
{
  int count = 1;
  while(num > 10)
  {
    num = num/10;
    count ++;
  }
  return count;
}

int32_t raw_samples[512];

void loop()
{
  int total = 0;
  
  for(int j=0;j<5;j++){
    
    size_t bytes_read = 0;
    i2s_read(I2S_NUM_0, raw_samples, sizeof(int32_t) * 512, &bytes_read, portMAX_DELAY);
    int samples_read = bytes_read / sizeof(int32_t);
    
    int32_t maximum = 0;
    for (int i = 0; i < samples_read; i++)
    {
      if(raw_samples[i] > maximum)
      {
        maximum = raw_samples[i];
      }
    }
    total = total + maximum;
  }

  total = total/5;
  int numLength = findLength(total);
  
  WiFiClient client;
  if (!client.connect(host, port)) {
    delay(1000);
    return;
  }
  else{
    numLength = numLength + 14;
    client.printf("POST /localhost HTTP/1.1\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: %d\r\n\r\nM%02x%02x%02x%02x%02x%02x,%ld",numLength,id[0],id[1],id[2],id[3],id[4],id[5],total);
    Serial.printf("POST /localhost HTTP/1.1Content-Type: text/html; charset=UTF-8Content-Length: %dM%02x%02x%02x%02x%02x%02x,%ld\n",numLength,id[0],id[1],id[2],id[3],id[4],id[5],total);
    client.stop();  
  }
    
  
    
    
    
 }

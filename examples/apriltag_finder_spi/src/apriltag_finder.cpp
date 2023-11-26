#include <Arduino.h>
#include <MSPIM.h>
#include <SPI.h>

#include <openmv.h>

OpenMV camera;

void setup()
{
  Serial.begin(115200);
  delay(1000);

  digitalWrite(CS_MV, HIGH);
  pinMode(CS_MV, OUTPUT);
  digitalWrite(CS_MV, HIGH);
  
  SPI.begin();
  //mSPI.Init();
 
  Serial.println(F("Welcome."));
}

uint8_t FindAprilTags()
{
    uint8_t tagCount = camera.getTagCountSPI();

    if(tagCount && tagCount != 0xFF) 
    {
      Serial.println(tagCount);
      for(int t = 0; t < tagCount; t++)
      {
        AprilTagDatum tag;
        if(camera.readTagSPI(tag))
        {
          Serial.print(F("Tag [cx="));
          Serial.print(tag.cx);
          Serial.print(F(", cy="));
          Serial.print(tag.cy);
          Serial.print(F(", w="));
          Serial.print(tag.w);
          Serial.print(F(", h="));
          Serial.print(tag.h);
          Serial.print(F(", id="));
          Serial.print(tag.id);
          Serial.print(F(", rot="));
          Serial.print(tag.rot);
          Serial.println(F("]"));
        }
      }
    }

    return tagCount;
}

void loop() 
{ 
  delay(10); //calm things down for a sec...
  FindAprilTags();
}

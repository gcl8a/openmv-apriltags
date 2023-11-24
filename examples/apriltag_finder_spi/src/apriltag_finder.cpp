#include <Arduino.h>
#include <SPI.h>
#include <openmv.h>

OpenMV camera;

void setup()
{
  Serial.begin(115200);
  delay(1000);

  SPI.begin();
 
  Serial.println(F("Welcome."));
}

uint8_t FindAprilTags()
{
    uint8_t tagCount = camera.getTagCountSPI();

    if(tagCount && tagCount != 0xFF) 
    {
      Serial.println(tagCount);
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

    return tagCount;
}

void loop() 
{ 
  delay(1); //calm things down for a sec...
  FindAprilTags();
}

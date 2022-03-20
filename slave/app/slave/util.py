pixel_ring_working = True

try:
	from pixel_ring import pixel_ring
except Exception:
	pixel_ring_working = False
	print ("Pixel ring was found not to work, disabling it")

class PixelRingWrapper:
	def off(self):
		if pixel_ring_working:
			pixel_ring.off()

	def think(self):
		if pixel_ring_working:
			pixel_ring.think()

	def speak(self):
		if pixel_ring_working:
			pixel_ring.speak()

	def wakeup(self):
		if pixel_ring_working:
			pixel_ring.wakeup()
	
	def set_volume(self, vol):
		if pixel_ring_working:
			pixel_ring.set_volume(vol)

pixel_ring_wrapper = PixelRingWrapper()

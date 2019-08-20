import time
import wave

try:
    import azure.cognitiveservices.speech as acss
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

speech_key, service_region = "218cdebfe0e449f18696ab8c17b009f6", "westus"

def speech_recognize(filename):
    speech_config = acss.SpeechConfig(subscription = speech_key, region = service_region)
    audio_config = acss.audio.AudioConfig(filename = filename)
    speech_recognizer = acss.SpeechRecognizer(speech_config = speech_config, audio_config = audio_config)
    recognized_text = []
    dirty_text = " "
    done = False

    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True
        
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: recognized_text.append(evt.result.text))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)
    
    return dirty_text.join(recognized_text)

import clsx from "clsx";
import { useEffect } from "react";
import { useVoiceVisualizer, VoiceVisualizer } from "react-voice-visualizer";

const MicRecorder = ({
  hide,
  submitMsg,
  setTranscribing,
}: React.HTMLAttributes<HTMLDivElement> & {
  hide: boolean;
  setTranscribing: React.Dispatch<React.SetStateAction<boolean>>;
  submitMsg: (msg: string) => Promise<void>;
}) => {
  const recorderControls = useVoiceVisualizer();
  const {
    // ... (Extracted controls and states, if necessary)
    recordedBlob,
    error,
    startRecording,
    stopRecording,
  } = recorderControls;

  useEffect(() => {
    let timeout: number;
    if (hide) timeout = setTimeout(() => stopRecording(), 400);
    else startRecording();
    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [hide]);

  // Get the recorded audio blob
  useEffect(() => {
    async function getTranscript() {
      if (!recordedBlob) return;
      setTranscribing(true);
      const file = new File([recordedBlob], "recording.webm", {
        type: "audio/webm",
      });
      const formData = new FormData();
      formData.append("audio", file); // "audio" must match your backend's field name

      const res = await fetch("http://localhost:8000/transcribe", {
        method: "POST",
        body: formData,
      });
      const data = (await res.json()) as { text: string };
      setTranscribing(false);
      await submitMsg(data.text);
    }

    getTranscript();
  }, [recordedBlob]);

  // Get the error when it occurs
  useEffect(() => {
    if (!error) return;

    console.error(error);
  }, [error]);

  return (
    <div
      className={clsx(
        "absolute left-1/2 -translate-x-1/2 -translate-y-12 bg-white border-2 border-zinc-700/10 rounded-2xl duration-400",
        hide ? "opacity-0" : "opacity-100",
        hide ? "-bottom-0.5" : "bottom-2"
      )}
    >
      <div className="absolute -top-[5px] -right-[5px] bg-red-500 w-[15px] h-[15px] rounded-full" />
      <div
        className="absolute -top-[5px] -right-[5px] bg-red-500 w-[15px] h-[15px] rounded-full animate-ping opacity-20"
        style={{ animationDuration: "1.3s" }}
      />
      <VoiceVisualizer
        controls={recorderControls}
        width={125}
        barWidth={2}
        height={100}
        rounded={5}
        isControlPanelShown={false}
        onlyRecording={true}
        secondaryBarColor="#fff"
        mainBarColor="#009966"
      />
    </div>
  );
};
export default MicRecorder;

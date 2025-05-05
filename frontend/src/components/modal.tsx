import Button from "./button";

const Modal = ({ modalFunc }: { modalFunc: (b: boolean) => void }) => {
  const handleSwitchUser = () => {};

  return (
    <>
      <div
        onClick={() => modalFunc(false)}
        className="bg-black/20 absolute top-0 left-0 h-screen w-screen"
      />
      <div className="bg-white p-2 rounded-xl absolute flex flex-col gap-2 z-10 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <h1 className="font-bold">Current User</h1>
        <input
          type="text"
          id="username"
          placeholder="Enter your username"
          className="border-2 border-zinc-300 bg-zinc-200 rounded-xl p-1 outline-0"
        />
        <div className="flex justify-between px-5">
          <Button onClick={() => modalFunc(false)}>Cancel</Button>
          <Button onClick={handleSwitchUser}>Save</Button>
        </div>
      </div>
    </>
  );
};
export default Modal;

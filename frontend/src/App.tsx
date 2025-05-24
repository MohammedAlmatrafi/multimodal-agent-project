import Chat from "./components/chat";
import Sidebar from "./components/sidebar";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
// @ts-expect-error the import isnt working
import "@fontsource/philosopher"; // npm install @fontsource/philosopher
// @ts-expect-error the import isnt working
import "@fontsource/nunito"; // npm install @fontsource/philosopher

TimeAgo.addDefaultLocale(en);

function App() {
  return (
    <main className="flex max-h-screen min-h-screen max-w-screen min-w-screen bg-zinc-100 gap-5 p-5">
      <Sidebar />
      <Chat />
    </main>
  );
}

export default App;

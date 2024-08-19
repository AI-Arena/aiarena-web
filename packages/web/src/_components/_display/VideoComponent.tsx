import React from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

const VideoComponent = ({ source }: { source: string }) => {
  const router = useRouter();

  const handleRedirect = (path: string) => {
    router.push(path);
  };
  return (
    <div
      style={{
        width: "100%",
        height: "85vh",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <video
        src={source}
        autoPlay
        loop
        muted
        playsInline
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 1,
          opacity: 1, // Initial opacity
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0) 100%)", // For Webkit browsers
        }}
      />
      {/* Tint overlay with matching fade-out effect */}
      <div
        className="absolute inset-0 bg-black pointer-events-none"
        style={{
          zIndex: 1,
          opacity: 0.6,
          maskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, rgba(0, 0, 0, 0.5) 70%, rgba(0, 0, 0, 0) 100%)",
        }}
      ></div>

      {/* Overlay content */}
      <div className="video-overlay absolute inset-0 flex flex-col justify-center items-center text-center text-white px-4">
        <h1 className="text-4xl font-bold mb-8 flex">
          {" "}
          <Image
            className="pr-2"
            src={"/ai-arena-logo.png"}
            alt="AI-arena-logo"
            width={50}
            height={50}
          ></Image>{" "}
          AI Arena
        </h1>
        <h2 className="text-2xl mb-8">Compete with your AI models</h2>
        <div className="flex flex-wrap justify-around w-80">
          <button
            onClick={() => handleRedirect("https://aiarena.net/stream/")}
            className="
    hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform "
          >
            {/* hover:border-4 hover:border-blue-500 */}
            Watch
          </button>
          <button
            onClick={() => handleRedirect("/play")}
            className="hover:border-4 border-4 border-customGreen bg-customGreen hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform "
          >
            Play
          </button>

          <button className="bg-gradient-green-lime text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-green-olive text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-green-yellow text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-1 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-2 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-gradient-experimental-3 text-white font-bold py-2 px-4 rounded">
            Button
          </button>
          <button className="bg-green-teal-gradient text-white font-bold py-2 px-4 rounded-lg border-2 border-softTeal hover:bg-softTeal">
  Green to Teal
</button>
<button className="bg-green-yellow-gradient text-white font-bold py-2 px-4 rounded-xl border-2 border-mellowYellow hover:bg-mellowYellow">
  Green to Yellow
</button>
<button className="bg-teal-yellow-gradient text-white font-bold py-2 px-4 rounded-lg border-2 border-customGreen hover:bg-customGreen">
  Teal to Yellow
</button>
        </div>
      </div>
    </div>
  );
};

export default VideoComponent;

// return (
//   <div style={{ width: '100%', height: '75vh', position: 'relative', overflow: 'hidden' }}>
//     <video
//       src={source}
//       autoPlay
//       loop
//       muted
//       playsInline
//       style={{
//         width: '100%',
//         height: '100%',
//         objectFit: 'cover',
//       }}
//     />
//     {/* Tint overlay */}
//     <div className="absolute inset-0 bg-black opacity-20 pointer-events-none"></div>

//     {/* Overlay content */}
//     <div className="video-overlay absolute inset-0 flex flex-col justify-center items-center text-center text-white px-4">
//       <h1 className="text-4xl font-bold mb-8">AI Arena</h1>
//       <h2 className="text-2xl mb-8">Compete with your AI models</h2>
//       <div className="flex flex-wrap justify-around w-full">
//         <button
//           onClick={() => handleRedirect('/watch')}
//           className="bg-blue-500 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-full shadow-lg transition duration-300 ease-in-out transform hover:scale-105 mb-4 md:mb-0"
//         >
//           Watch
//         </button>
//         <button
//           onClick={() => handleRedirect('/play')}
//           className="bg-green-500 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-full shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
//         >
//           Play
//         </button>
//       </div>
//     </div>
//   </div>
// );
// };

// export default VideoComponent;

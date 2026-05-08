import { ImageResponse } from "next/og";

// Next.js metadata icon route — genera /icon automáticamente.
// https://nextjs.org/docs/app/api-reference/file-conventions/metadata/app-icons

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#7C3AED", // electric-violet
          color: "white",
          fontSize: 20,
          fontWeight: 700,
          fontFamily: "ui-sans-serif, system-ui",
          borderRadius: 6,
        }}
      >
        S
      </div>
    ),
    { ...size },
  );
}

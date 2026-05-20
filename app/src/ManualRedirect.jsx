import { useEffect } from "react";

/** Redirect /manual and /manual/ to the static HTML in public/manual/. */
const ManualRedirect = () => {
  useEffect(() => {
    window.location.replace(
      `/manual/index.html${window.location.search}${window.location.hash}`
    );
  }, []);

  return (
    <div className="container py-5 text-center">
      <p>Abriendo manual de usuario…</p>
    </div>
  );
};

export default ManualRedirect;

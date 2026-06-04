function AbstainPanel({ reason }) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
      <div className="text-sm font-semibold text-amber-800">Not enough signal to call this</div>
      <p className="mt-1 text-sm text-amber-700">
        MedMaps is staying quiet on purpose ({reason}). A confident guess here would be worse
        than no guess at all.
      </p>
    </div>
  );
}

export default AbstainPanel;

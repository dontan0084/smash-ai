import cv2

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        break

    cv2.imshow("Smash", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()